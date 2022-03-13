import {filter, IEntity, ITextSearchFilter, orm, Storage} from "@dp/prototype";
import {ICreateCommand, IDeleteCommand, IUpdateCommand} from "@dp/prototype/src/model/cmd";

type EmailStatus = "draft" | "sent" | "deleted"

@Storage.database({table:"email"})
export class Email implements IEntity<string> {
    id?: string
    from:string
    to?:string
    subject?:string
    body?:string
    status:EmailStatus
    isOut:boolean
    isSeen:boolean
    ts:Date

/*
    @orm.field({column:"is_draft"})
    isDraft:boolean=true
*/
}

export class EmailShort implements DTO<Email> {
    id:Email["id"]
    subject:String
    ts:Date
}

export class EmailFilter implements ITextSearchFilter<Email> {
    @filter({op:".."})
    ts?:Date;

    @filter<Email>({op:"T",fields:["subject","body","to","from"]})
    /**
     * Полнотекстовый поиск бла бла бла
     */
    term?: string;
}

/**
 * Создает черновик
 */
export class EmailCreateDraftCommand implements ICreateCommand<Email>{
    from?:string
    to?:string
    subject?:string
    body?:string
}


/**
 * Изменяет черновик
 */
export class EmailSaveDraftCommand implements IUpdateCommand<Email> {
    id: Email["id"];

    from?:string
    to?:string
    subject?:string
    body?:string
}


/**
 * Отправляеет письмо
 */
export class EmailSendCommand implements IUpdateCommand<Email> {
    id: Email["id"];
}

/**
 * Удаляет черновик
 */
export class EmailDeleteDraftCommand implements IDeleteCommand<Email> {
    id: Email["id"];
}
